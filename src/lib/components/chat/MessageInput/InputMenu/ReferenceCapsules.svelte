<script lang="ts">
	import { getContext, onDestroy, onMount } from 'svelte';

	import { getReferenceCapsules, type ReferenceCapsule } from '$lib/apis/referenceCapsules';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import BookOpen from '$lib/components/icons/BookOpen.svelte';
	import SearchInput from './SearchInput.svelte';

	type PickerItem = ReferenceCapsule & {
		type: 'reference_capsule';
		name: string;
		description: string;
		status: 'processed';
	};

	const i18n: any = getContext('i18n');
	export let onSelect: (item: PickerItem) => void = () => {};

	let loaded = false;
	let loading = false;
	let items: PickerItem[] = [];
	let selectedIdx = 0;
	let query = '';
	let searchedQuery = '';
	let initialized = false;
	let searchDebounceTimer: ReturnType<typeof setTimeout>;
	let requestId = 0;

	$: if (initialized && query !== searchedQuery) {
		clearTimeout(searchDebounceTimer);
		searchDebounceTimer = setTimeout(load, 200);
	}

	const load = async () => {
		requestId += 1;
		const activeRequestId = requestId;
		searchedQuery = query;
		loading = true;
		const result = await getReferenceCapsules(localStorage.token, query.trim()).catch(() => []);
		if (activeRequestId !== requestId) return;
		items = (result ?? []).map((capsule) => ({
			...capsule,
			type: 'reference_capsule',
			name: capsule.title,
			description: capsule.summary,
			status: 'processed'
		}));
		selectedIdx = items.length ? 0 : -1;
		loading = false;
		loaded = true;
	};

	onMount(async () => {
		await load();
		initialized = true;
	});

	onDestroy(() => {
		clearTimeout(searchDebounceTimer);
	});
</script>

{#if loaded}
	<div
		class="flex min-h-0 flex-1 flex-col gap-0.5 overflow-hidden"
		data-testid="reference-capsule-picker"
	>
		<SearchInput bind:value={query} placeholder={$i18n.t('Search References')} />

		<div class="min-h-0 flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin">
			{#if items.length === 0 && loading}
				<div class="py-4.5"><Spinner /></div>
			{:else if items.length === 0}
				<div class="flex flex-col items-center gap-1 px-4 py-4 text-center text-xs text-gray-500">
					<BookOpen className="mb-1 size-5 opacity-60" />
					<div>{$i18n.t('No saved references found')}</div>
					<div class="text-[11px] text-gray-400">
						{$i18n.t('Open a chat’s actions menu and choose Save as Reference.')}
					</div>
				</div>
			{:else}
				<div class="flex flex-col gap-0.5">
					{#each items as item, idx}
						<button
							data-testid={`reference-capsule-option-${item.id}`}
							class="min-h-[2.25rem] w-full rounded-xl px-2 py-1 text-left text-[13px] font-normal {idx ===
							selectedIdx
								? 'bg-gray-50/40 dark:bg-gray-800/40 dark:text-gray-100 selected-command-option-button'
								: ''}"
							type="button"
							on:click={() => onSelect(item)}
							on:mousemove={() => (selectedIdx = idx)}
						>
							<Tooltip content={item.description} placement="top-start">
								<div
									class="flex min-w-0 items-center justify-between gap-2 text-black dark:text-gray-100"
								>
									<div class="min-w-0 flex-1 truncate">{item.name}</div>
									{#if item.stale}
										<span
											class="shrink-0 rounded-full bg-amber-100 px-1.5 py-0.5 text-[9px] text-amber-800 dark:bg-amber-950/50 dark:text-amber-200"
										>
											{$i18n.t('Source changed')}
										</span>
									{/if}
								</div>
								{#if item.tags?.length}
									<div class="mt-0.5 truncate text-[10px] text-gray-400">
										{item.tags.join(' · ')}
									</div>
								{/if}
							</Tooltip>
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</div>
{:else}
	<div class="py-4.5"><Spinner /></div>
{/if}
