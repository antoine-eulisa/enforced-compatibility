#!/usr/bin/python3

import json
import os
import sys
import logging 
from dataclasses import dataclass, field

@dataclass
class Version:
    major:int 
    minor:int
    patch:int

@dataclass
class Dependency:
    name: str 
    version: Version 
    
@dataclass
class System:
    path: str 
    name: str 
    versions: [Version]
    dependencies: [Dependency] = field(default_factory=list)
     

def buildVersion(versionAsString, path):
    components = versionAsString.split('.')
    if len(components) != 3:
      raise ValueError(f"version={versionAsString} format is invalid, should use [0-9]+\\.[0-9]+\\.[0-9]+\\. Found in {path}")
    try:
      return Version(major=int(components[0]),
          minor=int(components[1]),
          patch=int(components[2]))
    except Exception as e :
        logging.exception(f"Error processing version={versionAsString} in {path}")
        raise e

def buildDependency(dependency, path):
    return Dependency(name=dependency['name'], version=buildVersion(dependency['version'], path))


directory = sys.argv[1] if len(sys.argv) > 1 else "."

installed_versions = {}
visited_directories= [] 

#loading all files, doing individual file validation, unique identifiers validation and topology validation

for dirpath, _, filenames in os.walk(directory):
    for name in filenames:
        if name.endswith(".json"):
            path = os.path.join(dirpath, name)
            try:
                with open(path) as f:
                    has_recursive_json_files = any(((match := visited) in dirpath or dirpath in visited) for visited in visited_directories)
                    if has_recursive_json_files:
                        raise ValueError(f"file={path} was found in directory {dirpath}, but that's either the parent or the children of an already seen directory containing another JSON file, {match}. The already seen directories are {visited_directories}")
                    visited_directories.append(dirpath)
                    data = json.load(f)
                    name = data.get("name")
                    if name in installed_versions:
                        raise ValueError(f"project name={name} is defined twice, the first time in {installed_versions[name].path} and the second time in {path}")
                    versions = data.get("versions")
                    dependencies = data.get("dependencies")
                    #print(f"dep={dependencies}")
                    installed_versions[name] = System(path=path, 
                        name=name, 
                        versions=list(map(lambda v: buildVersion(v, path), versions)),
                        dependencies=list(map(lambda d: buildDependency(d, path), dependencies)) )
                    #print(f"{path}: name={name}")
                    #print(f"versions = {versions}")
                    #print(f"versions = {installed_versions}")

            except Exception as e:
                logging.exception(f"Error processing {path}")
                raise e

#print(f"versions = {installed_versions}")

#now iterating over all installations to make sure their dependencies are correctly met

errors = []

for installation_name in installed_versions:
    major_versions = []
    for version in installed_versions[installation_name].versions:
        if version.major in major_versions:
            errors.append(f"{installation_name} has multiple versions deployed with the same major number, either those are backward compatible and only one version should be used or different major numbers should be used, installed versions are {installed_versions[installation_name].versions}")
        major_versions.append(version.major)
        
    for dependency in installed_versions[installation_name].dependencies:
        if dependency.name in installed_versions:
            versions_of_this_dependency = installed_versions[dependency.name].versions
            if len(versions_of_this_dependency) > 0:
                good_version_found = False
                for dependency_installed_version in installed_versions[dependency.name].versions:
                    if dependency_installed_version.major == dependency.version.major \
                        and dependency_installed_version.minor >= dependency.version.minor \
                        and (dependency_installed_version.minor > dependency.version.minor or dependency_installed_version.patch >= dependency.version.patch):
                        good_version_found = True
                        break
                if not good_version_found:
                    errors.append(f"installed {installation_name} is dependent on {dependency.name} version {dependency.version}, but the only installed versions are {versions_of_this_dependency}")
            else:
                errors.append(f"installed {installation_name} is dependent on {dependency.name} (version {dependency.version}), and it's listed but without version")
        else:
            errors.append(f"installed {installation_name} is dependent on {dependency.name} (version {dependency.version}), but it's not installed, under any version ")

print("")
if len(errors) > 0:
    raise ValueError(f"failed dependencies {errors}")
else:
    print("ALL GOOD!")
