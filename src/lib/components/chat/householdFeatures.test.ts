import { describe, expect, it } from 'vitest';
import {
	getStoredHouseholdFeatures,
	modelAllowsHouseholdCodeInterpreter,
	modelAllowsHouseholdWebSearch,
	restoreHouseholdFeatureControls
} from './householdFeatures';

describe('household chat feature controls', () => {
	it('serializes opt-in controls into the server-side chat payload', () => {
		expect(getStoredHouseholdFeatures(true, false)).toEqual({
			memory: false,
			chat_history: false,
			web_search: true,
			code_interpreter: false
		});
	});

	it('restores each chat independently without leaking the previous chat state', () => {
		const enabledChat = restoreHouseholdFeatureControls(
			{ web_search: true, code_interpreter: true },
			{ webSearchEnabled: false, codeInterpreterEnabled: false }
		);
		const disabledChat = restoreHouseholdFeatureControls(
			{ web_search: false, code_interpreter: false },
			enabledChat
		);

		expect(enabledChat).toEqual({ webSearchEnabled: true, codeInterpreterEnabled: true });
		expect(disabledChat).toEqual({ webSearchEnabled: false, codeInterpreterEnabled: false });
	});

	it('keeps model defaults for legacy chats that have no stored controls', () => {
		expect(
			restoreHouseholdFeatureControls(undefined, {
				webSearchEnabled: true,
				codeInterpreterEnabled: false
			})
		).toEqual({ webSearchEnabled: true, codeInterpreterEnabled: false });
	});

	it('requires both the advertised capability and the backend builtin policy', () => {
		expect(modelAllowsHouseholdWebSearch(undefined)).toBe(false);
		expect(
			modelAllowsHouseholdWebSearch({
				info: { meta: { capabilities: { web_search: true }, builtinTools: { web_search: true } } }
			})
		).toBe(true);
		expect(
			modelAllowsHouseholdWebSearch({
				info: { meta: { capabilities: { web_search: true }, builtinTools: { web_search: false } } }
			})
		).toBe(false);
	});

	it('does not advertise Code Interpreter when the backend builtin policy disables it', () => {
		expect(modelAllowsHouseholdCodeInterpreter(undefined)).toBe(false);
		expect(
			modelAllowsHouseholdCodeInterpreter({
				info: {
					meta: {
						capabilities: { code_interpreter: true },
						builtinTools: { code_interpreter: true }
					}
				}
			})
		).toBe(true);
		expect(
			modelAllowsHouseholdCodeInterpreter({
				info: {
					meta: {
						capabilities: { code_interpreter: true },
						builtinTools: { code_interpreter: false }
					}
				}
			})
		).toBe(false);
	});
});
