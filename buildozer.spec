[app]

title = SoulTether
package.name = soultether
package.domain = org.soultether

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0.0

requirements = python3,kivy,swisseph,pymeeus,requests

permissions = INTERNET

orientation = portrait
fullscreen = 0

[buildozer]

log_level = 2
warn_on_root = 1

ios.version = 14.0
ios.family = iphone
ios.codesign_identity = iPhone Developer
ios.provisioning_profile_specifier = 

kivy_version = 2.2.1
