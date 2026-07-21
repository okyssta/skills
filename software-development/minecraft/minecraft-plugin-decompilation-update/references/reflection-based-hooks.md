# Reflection-Based Optional Dependency Pattern

When rebuilding plugins for modern Paper versions, optional plugin hooks (WorldGuard, Skript,
PlaceholderAPI, etc.) that previously relied on compile-time dependencies often break due to
version conflicts, missing Maven artifacts, or incompatible transitive deps.

## The Problem

compileOnly 'com.sk89q.worldguard:worldguard-bukkit:7.0.12'
compileOnly 'ch.njol:skript:2.9.4'

These cause cascading failures:
- WorldGuard pins Guava 32.1.3-jre, Paper needs 33.3.1-jre → resolve FAILURE
- Skript has NO Maven artifact → compile FAILURE
- PlaceholderAPI repo may be down → build FAILURE

## The Fix: 100% Reflection-Based Hooks

Replace ALL compile-time dependencies for optional plugins with reflection. The plugin only
needs Paper API at compile time. Hook classes are loaded at runtime only when the target
plugin is present.

### Structure

YourPlugin.java — No optional-plugins imports at all
gui/WorldGuardUtil.java — Reflection-based WG region check
hooks/SkriptHook.java — Reflection-based Skript event registration
utils/wg/BlacklistedRegion.java — Calls WorldGuardUtil

### WorldGuard Region Check (Reflection)

```java
public class WorldGuardUtil {
    private static boolean checked = false, available = false;
    private static Object worldGuardInstance;
    private static Method getPlatform, getRegionContainer, createQuery,
                         getApplicableRegions, adaptLocation, getRegions, getId;

    public static boolean isInRegion(Player player, String regionName) {
        if (!isAvailable()) return false;
        try {
            Object platform = getPlatform.invoke(worldGuardInstance);
            Object container = getRegionContainer.invoke(platform);
            Object query = createQuery.invoke(container);
            Object adaptedLoc = adaptLocation.invoke(null, player.getLocation());
            for (Object region : (Iterable<?>) getRegions.invoke(
                    getApplicableRegions.invoke(query, adaptedLoc))) {
                if (((String) getId.invoke(region)).equalsIgnoreCase(regionName))
                    return true;
            }
        } catch (Exception ignored) { }
        return false;
    }

    public static boolean isAvailable() {
        if (!checked) try {
            Class<?> wg = Class.forName("com.sk89q.worldguard.WorldGuard");
            worldGuardInstance = wg.getMethod("getInstance").invoke(null);
            getPlatform = wg.getMethod("getPlatform");
            Class<?> platform = getPlatform.getReturnType();
            getRegionContainer = platform.getMethod("getRegionContainer");
            createQuery = getRegionContainer.getReturnType().getMethod("createQuery");
            Class<?> queryClass = createQuery.getReturnType();
            getApplicableRegions = queryClass.getMethod("getApplicableRegions",
                Class.forName("com.sk89q.worldedit.util.Location"));
            adaptLocation = Class.forName("com.sk89q.worldedit.bukkit.BukkitAdapter")
                .getMethod("adapt", Location.class);
            getRegions = getApplicableRegions.getReturnType().getMethod("getRegions");
            getId = Class.forName(
                "com.sk89q.worldguard.protection.regions.ProtectedRegion")
                .getMethod("getId");
            available = true;
        } catch (Exception ignored) { checked = true; }
        return available;
    }
}
```

### Skript Hook (Reflection)

```java
public class SkriptHook {
    public void of() {
        if (Bukkit.getPluginManager().getPlugin("Skript") == null) return;
        try {
            Class<?> sk = Class.forName("ch.njol.skript.Skript");
            Method register = sk.getMethod("registerEvent",
                String.class, Class.class, Class.class, String[].class);
            register.invoke(null, "Kit Load",
                Class.forName("ch.njol.skript.lang.util.SimpleEvent"),
                KitLoadEvent.class, new String[]{"[kit] load"});
            // register more events...
        } catch (Exception e) {
            plugin.getLogger().warning("Skript hook failed: " + e.getMessage());
        }
    }
}
```

### Clean build.gradle

```groovy
dependencies {
    compileOnly 'io.papermc.paper:paper-api:1.21.4-R0.1-SNAPSHOT'
    // NO WorldGuard, WorldEdit, Skript, PlaceholderAPI
}
```

### When to Use / Not Use

**Use reflection when:**
- The plugin is optional (not required for core features)
- Dependency has version conflicts with Paper API
- Dependency not available in standard Maven repos
- You only need basic API calls (region check, event registration)
- Graceful degradation is acceptable

**Don't use reflection when:**
- The plugin is required for core features
- You need complex API calls with interfaces/callbacks
- Dependency IS available with compatible versions

## Dependency Constraint Conflicts

WorldGuard 7.0.12 pins Guava 32.1.3-jre, but Paper API 1.21.4 needs 33.3.1-jre.
Gradle cannot satisfy both due to `strictly` semantics. Fix: remove the conflicting
dependency and use reflection — at runtime the server's own WG jar provides classes.

## Custom GUI System (Replace Bundled Library)

```java
public class GuiBuilder {
    protected final Inventory inventory;
    protected final Map<Integer, Consumer<InventoryClickEvent>> handlers = new HashMap<>();

    public GuiBuilder(int size, String title) {
        this.inventory = Bukkit.createInventory(null, size, component(title));
    }

    public void setItem(int slot, ItemStack item, Consumer<InventoryClickEvent> handler) {
        inventory.setItem(slot, item);
        if (handler != null) handlers.put(slot, handler);
    }

    public void open(Player player) {
        var listener = new GuiListener(player);
        Bukkit.getPluginManager().registerEvents(listener, plugin);
        player.openInventory(inventory);
    }

    private class GuiListener implements Listener {
        @EventHandler void onClick(InventoryClickEvent e) {
            if (!e.getInventory().equals(inventory)) return;
            var h = handlers.get(e.getRawSlot());
            if (h != null) h.accept(e);
        }
        @EventHandler void onClose(InventoryCloseEvent e) {
            if (e.getInventory().equals(inventory)) HandlerList.unregisterAll(this);
        }
    }
}
```

Key: per-session listener with auto-unregister on close.

## Dynamic Command Registration

For commands like /kit1-/kitN (configurable count):

```java
public class DynamicCommand extends BukkitCommand {
    public DynamicCommand(JavaPlugin plugin, String name) {
        super(name);
        try {
            Field f = Bukkit.getServer().getClass().getDeclaredField("commandMap");
            f.setAccessible(true);
            ((CommandMap) f.get(Bukkit.getServer())).register(plugin.getName(), this);
        } catch (Exception e) {
            plugin.getLogger().warning("Failed to register /" + name);
        }
    }
}
```

## ColorizeText with Adventure API

```java
public class ColorizeText {
    static final Pattern HEX = Pattern.compile("&#([A-Fa-f0-9]{6})");

    public static String legacy(String text) {
        Matcher m = HEX.matcher(text);
        StringBuffer sb = new StringBuffer();
        while (m.find()) {
            var rep = new StringBuilder("§x");
            for (char c : m.group(1).toCharArray()) rep.append('§').append(c);
            m.appendReplacement(sb, Matcher.quoteReplacement(rep.toString()));
        }
        m.appendTail(sb);
        return sb.toString().replaceAll("&([0-9a-fk-or])", "§$1");
    }

    public static Component component(String text) {
        return LegacyComponentSerializer.legacySection().deserialize(legacy(text));
    }
}
```

## bStats Metrics

The Metrics class (~400 lines) can be included directly — zero dependencies beyond Java
and Bukkit API. Change the package name for the relocation check. Same for all chart
types: SingleLineChart, SimplePie, AdvancedPie, SimpleBarChart, DrilldownPie, etc.
