export type StoredHouseholdFeatures = {
	memory: false;
	chat_history: false;
	web_search: boolean;
	code_interpreter: boolean;
};

type FeatureDefaults = {
	webSearchEnabled: boolean;
	codeInterpreterEnabled: boolean;
};

export const getStoredHouseholdFeatures = (
	webSearchEnabled: boolean,
	codeInterpreterEnabled: boolean
): StoredHouseholdFeatures => ({
	memory: false,
	chat_history: false,
	web_search: Boolean(webSearchEnabled),
	code_interpreter: Boolean(codeInterpreterEnabled)
});

export const restoreHouseholdFeatureControls = (
	stored: Partial<StoredHouseholdFeatures> | null | undefined,
	defaults: FeatureDefaults
): FeatureDefaults => ({
	webSearchEnabled:
		typeof stored?.web_search === 'boolean' ? stored.web_search : defaults.webSearchEnabled,
	codeInterpreterEnabled:
		typeof stored?.code_interpreter === 'boolean'
			? stored.code_interpreter
			: defaults.codeInterpreterEnabled
});

export const modelAllowsHouseholdWebSearch = (model: any): boolean => {
	if (!model) return false;
	const meta = model?.info?.meta ?? {};
	return (meta?.capabilities?.web_search ?? true) && (meta?.builtinTools?.web_search ?? true);
};

export const modelAllowsHouseholdCodeInterpreter = (model: any): boolean => {
	if (!model) return false;
	const meta = model?.info?.meta ?? {};
	return (
		(meta?.capabilities?.code_interpreter ?? true) && (meta?.builtinTools?.code_interpreter ?? true)
	);
};
