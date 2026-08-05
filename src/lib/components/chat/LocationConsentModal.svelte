<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';

	export let show = false;
	export let busy = false;
	export let errorMessage = '';

	const dispatch = createEventDispatcher();
</script>

<Modal bind:show size="sm" className="bg-white dark:bg-gray-900 rounded-3xl overflow-hidden">
	<div class="px-6 py-6 text-gray-900 dark:text-white" data-testid="location-consent-modal">
		<div class="mb-2 text-lg font-medium">Use your device location?</div>
		<p class="text-sm leading-6 text-gray-600 dark:text-gray-300">
			This lets Local AI answer location-aware questions, such as local weather, even when you are
			away from the server.
		</p>
		<div
			class="mt-4 rounded-2xl bg-gray-50 px-4 py-3 text-xs leading-5 text-gray-600 dark:bg-white/5 dark:text-gray-300"
		>
			Your browser asks permission. Location refreshes while this app is open or resumed. Raw GPS
			coordinates are not saved; only a nearby city or region, accuracy, and update time are kept.
			You can change this later in Settings.
		</div>

		{#if errorMessage}
			<div
				class="mt-4 rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700 dark:bg-red-950/40 dark:text-red-200"
				role="alert"
			>
				{errorMessage}
			</div>
		{/if}

		<div class="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
			<button
				type="button"
				class="rounded-xl px-4 py-2.5 text-sm text-gray-600 transition hover:bg-gray-100 disabled:opacity-50 dark:text-gray-300 dark:hover:bg-white/10"
				disabled={busy}
				data-testid="location-consent-skip"
				on:click={() => dispatch('skip')}
			>
				Not now
			</button>
			<button
				type="button"
				class="rounded-xl bg-black px-4 py-2.5 text-sm text-white transition hover:bg-gray-800 disabled:cursor-wait disabled:opacity-60 dark:bg-white dark:text-black dark:hover:bg-gray-200"
				disabled={busy}
				data-testid="location-consent-allow"
				on:click={() => dispatch('allow')}
			>
				{busy ? 'Getting location…' : 'Use my location'}
			</button>
		</div>
	</div>
</Modal>
