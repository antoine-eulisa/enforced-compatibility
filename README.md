# Purpose

Provide a single source of truth for what was/is/is to be deployed, and where.

## How

This is achieved by storing in this git repository a collection of files. 

There is 1 file for 1 system.

Each file lists:

- the system name
- the versions deployed (usually one, but in case of backward incompatible changes being introduced multiple versions can be supported at the same time)
- the dependencies of this system, itself a list of systems and versions

Git branches are used to represent environments.

Git tags are used to represent deployments activities.

## Versions

The versions are expressed using [semantic versioning](https://semver.org/)

A version number is composed of MAJOR.MINOR.PATCH. Each compoment is incremented when:

- MAJOR version when you make incompatible changes that require your client to adapt its implementation.
- MINOR version when you add functionality in a backward compatible and planned manner
- PATCH version when you make backward compatible unplanned bug fixes

The version of a system is not necessarly aligned with the version of the ICD of this system. But each version should provide an explicit link to the supported ICD version.

# Constraints

A system can only be declared once all it's dependencies are found to be declared and of the correct version.

A dependency is found of the correct version as soon as it is deployed with a version respecting the following constraints:

- the dependency MAJOR number is the same as the expected one
- the dependency MINOR number is the same or above as the expected one
- if the dependency MINOR number is the same then the dependency PATCH number is the same or above as the expected one

## git hooks

A python script validates that the system declaration are correct, internally and in relatino of their constratints.

# Governance

Each system is responsible to provide the descriptor files for each new release.  

Typically merges are used to promote a deployment from OTH to PPE and onto PRD, unless we deploy a new instance directly in PPE or PRD.

The repository is consumed by:

- the MS, in order for them to get the proper references to the ICDs they need to interact with a given environment.
- the systems, to make sure their foreseen dependencies are actually planned to be deployed where they will deploy themselves.
- the agency, to ensure that no 2 systems have different expectations in regards of same dependency and its versions.

# Future evolution

1. support multiple versions for the dependencies too, in case a system has multiple versions deployed then each might require non-compatible version of a dependency.
1. validate than deployments respects the content of this repository. 