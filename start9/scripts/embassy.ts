import { compat } from "./deps.ts";

// Read config spec from config_spec.yaml
// Since we use type: script for config get/set, this just needs to export getConfig
// The actual config handling is done by get-config.sh and set-config.sh

export const getConfig = compat.getConfig({
  // Config spec is defined in config_spec.yaml file
  // When using type: script, Start9 reads the spec from the file
  // But we still need to export this for compatibility
});

export const setConfig = compat.setConfig(async (effects, config) => {
  // Not used when type: script is used
  return {};
});

export const properties = compat.properties;
export const dependencies = compat.dependencies;
export const migration = compat.migration;
