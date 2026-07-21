# Session Process: Decompiling and Updating XyrisKits, SpawnItemsX, and KitsX for Paper 26.1.2

This document records the specific process followed in this session to decompile and prepare three Minecraft plugins for updating to Paper 26.1.2 (Minecraft 1.21.4).

## Plugins Worked On
1. **SpawnItemsX-1.0.jar** - Simple kit/giver plugin
2. **XyrisKits-2.0.6-all.jar** - Comprehensive kit management system
3. **KitsX-1.0.3-all.jar** - Advanced kit system with ender chests, kit rooms, etc.

## Step-by-Step Process

### 1. Locating the Plugins
The plugins were found in a Pterodactyl volume:
- SpawnItemsX: `/var/lib/pterodactyl/volumes/f60fc6fd-aa68-4db3-9b41-348d36470117/plugins/SpawnItemsX-1.0.jar`
- XyrisKits: Located in `.paper-remapped/` directory as `XyrisKits-2.0.6-all (1).jar`
- KitsX: Located in `.paper-remapped/` directory as `KitsX-1.0.3-all (1).jar`

### 2. Preparation
```bash
# Created working directory structure
mkdir -p /tmp/mc-plugins/{decompile,decompiled/{SpawnItemsX,XyrisKits,KitsX},build}

# Copied JARs to decompile directory
cp "/var/lib/pterodactyl/volumes/f60fc6fd-aa68-4db3-9b41-348d36470117/plugins/SpawnItemsX-1.0.jar" /tmp/mc-plugins/decompile/
cp "/var/lib/pterodactyl/volumes/f60fc6fd-aa68-4db3-9b41-348d36470117/plugins/.paper-remapped/XyrisKits-2.0.6-all (1).jar" /tmp/mc-plugins/decompile/XyrisKits-2.0.6-all.jar
cp "/var/lib/pterodactyl/volumes/f60fc6fd-aa68-4db3-9b41-348d36470117/plugins/.paper-remapped/KitsX-1.0.3-all (1).jar" /tmp/mc-plugins/decompile/KitsX-1.0.3-all.jar
```

### 3. Installing Dependencies
- **Java 25** was required for Paper 26.1.2 (installed from Adoptium Temurin binaries)
- **Gradle 9.6.1** was used (supports Java 25)
- **CFR 0.152** decompiler was downloaded

### 4. Decompilation Process
```bash
# Downloaded CFR
curl -sL -o /tmp/cfr.jar "https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar"

# Decompiled each plugin
java -jar /tmp/cfr.jar /tmp/mc-plugins/decompile/SpawnItemsX-1.0.jar --outputdir /tmp/mc-plugins/decompiled/SpawnItemsX/
java -jar /tmp/cfr.jar /tmp/mc-plugins/decompile/XyrisKits-2.0.6-all.jar --outputdir /tmp/mc-plugins/decompiled/XyrisKits/
java -jar /tmp/cfr.jar /tmp/mc-plugins/decompile/KitsX-1.0.3-all.jar --outputdir /tmp/mc-plugins/decompiled/KitsX/
```

### 5. Code Analysis Findings

#### SpawnItemsX
- Simple plugin with 4 main Java classes
- Uses IridiumColorAPI for color formatting
- Dependencies: Bukkit API, IridiumColorAPI
- Gives players items with right-click commands from spawnitems.yml
- Main classes: Main, SpawnItems (CommandExecutor), Click and Interact listeners

#### XyrisKits
- Complex plugin using custom PluginWrapper framework
- Extensive use of Lombok annotations (@Data, @Builder, etc.)
- Uses Adventure API for text formatting (MiniMessage)
- Features: Kit editing, sharing, auto-rekit, PlaceholderAPI/WorldGuard/Skript hooks
- Modular architecture with managers: KitManager, PlayerKitsManager, KitSharingManager, AutoRekitManager
- Uses custom utility library (dev.darkxx.utils) with version checking, command builders, menu systems, etc.

#### KitsX
- Similar architecture to XyrisKits but more focused on kit management
- Features: Kits, premade kits, ender chest kits, kit rooms, auto-rekit
- Uses same utility library as XyrisKits
- Managers: KitUtil, PremadeKitUtil, EnderChestUtil, KitRoomUtil, AutoRekitUtil
- Advanced menu system with XMenu framework

### 6. Build Project Creation
For each plugin, a Gradle project was created with:
- Java 21 compatibility (for initial compilation attempt)
- Paper API dependency: `io.papermc.paper:paper-api:26.1.2.build.72-stable`
- Proper resource copying (plugin.yml, etc.)
- Standard Maven/Gradle directory structure

### 7. Java Version Compatibility Issue Encountered
During build attempts, discovered:
- Paper 26.1.2 requires **Java 25** (not 21)
- Gradle's dependency resolution complained about JVM version mismatch
- Even with Java 25 installed, Gradle still insisted on JVM 21 for the dependency
- This appears to be a metadata issue with the Paper API pom file

### 8. Workaround Identified
Research showed that:
- Paper 26.1.2 (MC 1.21.4) maintains API compatibility with Paper 1.21.4
- Can compile against `io.papermc.paper:paper-api:1.21.4-R0.1-SNAPSHOT` or similar
- Then run on actual Paper 26.1.2 server with Java 25
- The API surface remains compatible between these versions

## Key Learnings from This Session

1. **Paper Version vs Java Version Mapping**:
   - Paper 1.16.x: Java 8-16
   - Paper 1.17.x-1.18.x: Java 16
   - Paper 1.19.x-1.20.x: Java 17
   - Paper 1.21.x: Java 21
   - Paper 26.x: Java 25 (required for 26.1.2)

2. **Paper API Availability**:
   - Paper API versions are not always immediately available in Maven for the very latest builds
   - Using slightly older but compatible API versions for compilation is acceptable
   - The actual server runtime version determines features available

3. **Decompilation Best Practices**:
   - CFR handles most modern Java bytecode well
   - Check for obfuscation (these plugins were not obfuscated)
   - Examine plugin.yml and resource files first for feature overview
   - Focus on main classes, managers, and listeners for core logic

4. **Plugin Architecture Patterns Observed**:
   - Use of custom PluginWrapper framework (instead of extending JavaPlugin directly)
   - Heavy use of Lombok for boilerplate reduction
   - Modular manager pattern for separation of concerns
   - YAML-driven menu systems (extremely important for user customization)
   - Event-driven architecture with proper listener separation
   - Integration hooks for popular plugins (PlaceholderAPI, WorldGuard, Skript)

5. **Common Update Points for Newer Paper Versions**:
   - ChatColor replacement with Adventure API/TextComponent
   - Checking for deprecated method signatures
   - Verifying NMS code compatibility (if any)
   - Ensuring dependency versions are compatible
   - Validating plugin.yml syntax and API version

## Next Steps for Completion
To complete this task, the following would need to be done:
1. Fix the Java version/Gradle compatibility issue (use Java 25 for both compilation and runtime with appropriate Gradle version)
2. Address any API deprecations found in the decompiled code
3. Build the projects successfully
4. Test the resulting JARs on a Paper 26.1.2 server
5. Deploy the updated plugins back to the original server location

## Files Created in This Session
- Decompiled source code in `/tmp/mc-plugins/decompiled/`
- Gradle project structure for SpawnItemsX in `/tmp/mc-plugins/build/SpawnItemsX/` (incomplete due to Java version issues)
- Process documentation in this file