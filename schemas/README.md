# PreCICE Configuration Schema

This document provides an overview of the JSON Schema used for validating PreCICE configuration files. The schema is designed to ensure that configuration files adhere to the expected structure and data types required by PreCICE.

## Schema Overview

- **Schema Version**: The schema follows the JSON Schema draft-07 standard.

- **Root Type**: The root of the schema is an `object` with a required property `precice-configuration`.

## Key Properties

### precice-configuration

This is the main object containing several nested properties:

- **log**: Configures logging settings.
  - **sink**: Defines logging options such as `filter`, `format`, and `enabled` status.

- **data:vector**: An array of objects representing data vectors, each requiring a `@name` property.

- **mesh**: Defines mesh configurations, which can be either a single `meshItem` or an array of `meshItem` objects.

- **participant**: An array of participants, each with a `@name` and options for `provide-mesh`, `receive-mesh`, `read-data`, `write-data`, and more.

- **m2n:sockets**: Defines socket configurations for M2N communication.

- **coupling-scheme:serial-explicit**: Specifies the coupling scheme, which can be a single `couplingSchemeItem` or an array.

## Definitions

### meshItem

- **@name**: String identifier for the mesh.
- **@dimensions**: Specifies dimensions (1-3).
- **use-data**: Array of data usage specifications.

### m2nSocketItem

- **@acceptor**: Acceptor identifier.
- **@connector**: Connector identifier.
- **@exchange-directory**: Directory for data exchange.

### couplingSchemeItem

- **time-window-size**: Object specifying the time window size.
- **participants**: List of participants involved in the coupling scheme.
- **exchange**: Details of data exchange.

## Usage

This schema is used to validate JSON configuration files for PreCICE. Ensure that your configuration files conform to this schema to avoid errors during processing.

For more details on PreCICE and its configuration options, refer to the official [PreCICE documentation](TODO).
