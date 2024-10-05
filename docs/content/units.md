# Units

To create a consistent, comprehensive, and collaborative set of units for industrial ecology, life cycle assessment, material flow analysis, and other sustainability domains, we start with some existing catalogues.

Units are trickier than one might think - in our development, we found the following very helpful:

* [C++ Quantities and units library documentation](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3045r0.html#quick-domain-introduction)
* [User guide for QUDT](https://github.com/qudt/qudt-public-repo/wiki/User-Guide-for-QUDT)

## Unit organization and structure

Units are organized into a simple hierarchy:

1. Quantity type (ISO) / Quantity kind (QUDT)
2. Base unit, i.e. those whose value is 1 for all given conversion factors. We currently use the following base units:
    * Acidity: `PH` (Ph)
    * Amount of Substance: `MOL` (Mole)
    * Angle: `RAD` (Radian)
    * Count: `NUM` (Number)
    * Current: `A` (Ampere)
    * Energy: `J` (Joule)
    * Force: `N` (Newton)
    * Length: `M` (Meter)
    * Magnetic field: `T` (Tesla)
    * Mass: `GM` (Gram)
    * Power: `W` (Watt)
    * Pressure: `PA` (Pascal)
    * Resistance: `OHM` (Ohm)
    * Temperature: `K` (Kelvin)
    * Time: `S` (Second)
    * Voltage: `V` (Voltage)

3. Other units based on and with a hierarchical relationship to the base units, e.g. `MegaJ`, `M3`.

## QUDT (Quantities, Units, Dimensions, and Time)

[QUDT](https://qudt.org/) is the foundation that our unit systems are built on top of.

As QUDT is quite broad, we only need to use a subset



