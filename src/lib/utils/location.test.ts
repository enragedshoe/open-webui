import { afterEach, describe, expect, it, vi } from 'vitest';
import { getUserPositionDetails } from './index';

describe('getUserPositionDetails', () => {
	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it('returns browser coordinates with accuracy, capture time, and time zone', async () => {
		const getCurrentPosition = vi.fn(
			(resolve: PositionCallback, _reject: PositionErrorCallback, _options?: PositionOptions) =>
				resolve({
					coords: { latitude: 40.7128123, longitude: -74.0060123, accuracy: 42.4 },
					timestamp: Date.parse('2026-08-03T12:00:00Z')
				} as GeolocationPosition)
		);
		vi.stubGlobal('navigator', { geolocation: { getCurrentPosition } });

		const location = await getUserPositionDetails({ maximumAge: 1234 });

		expect(location.latitude).toBe(40.7128123);
		expect(location.longitude).toBe(-74.0060123);
		expect(location.accuracy).toBe(42.4);
		expect(location.capturedAt).toBe('2026-08-03T12:00:00.000Z');
		expect(getCurrentPosition).toHaveBeenCalledOnce();
		expect(getCurrentPosition.mock.calls[0][2]).toMatchObject({
			enableHighAccuracy: false,
			maximumAge: 1234,
			timeout: 15_000
		});
	});

	it('fails clearly when browser geolocation is unavailable', async () => {
		vi.stubGlobal('navigator', {});
		await expect(getUserPositionDetails()).rejects.toThrow('not supported');
	});
});
