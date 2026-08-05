<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	import {
		deleteReferenceCapsule,
		previewReferenceCapsule,
		saveReferenceCapsule,
		type ReferenceCapsulePreview
	} from '$lib/apis/referenceCapsules';
	import Modal from '$lib/components/common/Modal.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import BookOpen from '$lib/components/icons/BookOpen.svelte';

	const i18n: any = getContext('i18n');

	export let show = false;
	export let chatId = '';
	export let modelId = '';

	let loadedChatId = '';
	let loading = false;
	let saving = false;
	let preview: ReferenceCapsulePreview | null = null;
	let factsText = '';
	let decisionsText = '';
	let constraintsText = '';
	let openQuestionsText = '';
	let tagsText = '';

	const toLines = (items: string[] = []) => items.join('\n');
	const fromLines = (value: string) =>
		value
			.split('\n')
			.map((item) => item.replace(/^\s*[-*•]+\s*/, '').trim())
			.filter(Boolean);
	const fromTags = (value: string) =>
		value
			.split(',')
			.map((item) => item.trim())
			.filter(Boolean);

	const syncEditors = () => {
		factsText = toLines(preview?.facts);
		decisionsText = toLines(preview?.decisions);
		constraintsText = toLines(preview?.constraints);
		openQuestionsText = toLines(preview?.open_questions);
		tagsText = (preview?.tags ?? []).join(', ');
	};

	const loadPreview = async (regenerate = false) => {
		if (!chatId || loading) return;
		loading = true;
		preview = null;
		try {
			preview = await previewReferenceCapsule(localStorage.token, chatId, modelId, regenerate);
			syncEditors();
			loadedChatId = chatId;
		} catch (error) {
			console.error(error);
			toast.error(`${error}`);
			close();
		} finally {
			loading = false;
		}
	};

	const close = () => {
		show = false;
		loadedChatId = '';
		preview = null;
	};

	const save = async () => {
		if (!preview || saving) return;
		if (!preview.title.trim() || !preview.summary.trim()) {
			toast.error($i18n.t('A title and summary are required'));
			return;
		}

		saving = true;
		try {
			preview = {
				...preview,
				title: preview.title.trim(),
				summary: preview.summary.trim(),
				facts: fromLines(factsText),
				decisions: fromLines(decisionsText),
				constraints: fromLines(constraintsText),
				open_questions: fromLines(openQuestionsText),
				tags: fromTags(tagsText)
			};
			const saved = await saveReferenceCapsule(localStorage.token, preview);
			toast.success($i18n.t('Reference saved'));
			preview.existing_id = saved.id;
			close();
		} catch (error) {
			console.error(error);
			toast.error(`${error}`);
		} finally {
			saving = false;
		}
	};

	const remove = async () => {
		if (!preview?.existing_id) return;
		if (!window.confirm($i18n.t('Delete this saved reference?'))) return;
		try {
			await deleteReferenceCapsule(localStorage.token, preview.existing_id);
			toast.success($i18n.t('Reference deleted'));
			close();
		} catch (error) {
			console.error(error);
			toast.error(`${error}`);
		}
	};

	$: if (show && chatId && loadedChatId !== chatId && !loading) {
		loadPreview();
	}
</script>

<Modal bind:show size="md">
	<div data-testid="reference-capsule-modal">
		<div class="flex items-center justify-between px-5 pt-4 pb-2 dark:text-gray-200">
			<div class="flex min-w-0 items-center gap-2">
				<BookOpen className="size-4.5 shrink-0" />
				<div class="truncate text-sm font-medium">{$i18n.t('Save as Reference')}</div>
			</div>
			<button
				class="rounded-lg p-1 text-gray-500 transition hover:bg-gray-100 dark:hover:bg-gray-800"
				aria-label={$i18n.t('Close')}
				on:click={close}
			>
				<XMark className="size-4" />
			</button>
		</div>

		{#if loading}
			<div class="flex min-h-52 flex-col items-center justify-center gap-3 px-6 py-10">
				<Spinner className="size-5" />
				<div class="text-center text-sm text-gray-500">
					{$i18n.t('Creating a concise draft for you to review...')}
				</div>
			</div>
		{:else if preview}
			<div class="max-h-[75dvh] overflow-y-auto px-5 pb-5 scrollbar-thin">
				<div
					class="mb-4 rounded-2xl bg-blue-50 px-3.5 py-3 text-xs leading-5 text-blue-900 dark:bg-blue-950/40 dark:text-blue-200"
				>
					{$i18n.t(
						'Review this draft before saving. It will never be recalled automatically; you choose it from References when you want a later chat to use it.'
					)}
				</div>

				<div class="flex flex-col gap-3">
					<label class="flex flex-col gap-1 text-xs text-gray-600 dark:text-gray-300">
						<span>{$i18n.t('Title')}</span>
						<input
							data-testid="reference-capsule-title"
							class="w-full rounded-xl border border-gray-200 bg-transparent px-3 py-2 text-sm text-gray-900 outline-hidden focus:border-gray-400 dark:border-gray-700 dark:text-gray-100"
							maxlength="160"
							bind:value={preview.title}
						/>
					</label>

					<label class="flex flex-col gap-1 text-xs text-gray-600 dark:text-gray-300">
						<span>{$i18n.t('Summary')}</span>
						<textarea
							data-testid="reference-capsule-summary"
							class="min-h-28 w-full resize-y rounded-xl border border-gray-200 bg-transparent px-3 py-2 text-sm leading-5 text-gray-900 outline-hidden focus:border-gray-400 dark:border-gray-700 dark:text-gray-100"
							maxlength="8000"
							bind:value={preview.summary}
						></textarea>
					</label>

					<label class="flex flex-col gap-1 text-xs text-gray-600 dark:text-gray-300">
						<span
							>{$i18n.t('Tags')}
							<span class="text-gray-400">({$i18n.t('comma separated')})</span></span
						>
						<input
							data-testid="reference-capsule-tags"
							class="w-full rounded-xl border border-gray-200 bg-transparent px-3 py-2 text-sm text-gray-900 outline-hidden focus:border-gray-400 dark:border-gray-700 dark:text-gray-100"
							bind:value={tagsText}
						/>
					</label>

					<details class="rounded-2xl border border-gray-100 px-3.5 py-2 dark:border-gray-800">
						<summary
							class="cursor-pointer select-none text-xs font-medium text-gray-700 dark:text-gray-200"
						>
							{$i18n.t('Structured details')}
						</summary>
						<div class="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
							{#each [{ label: $i18n.t('Facts'), value: 'facts' }, { label: $i18n.t('Decisions'), value: 'decisions' }, { label: $i18n.t('Constraints'), value: 'constraints' }, { label: $i18n.t('Open questions'), value: 'questions' }] as field}
								<label class="flex flex-col gap-1 text-xs text-gray-600 dark:text-gray-300">
									<span
										>{field.label}
										<span class="text-gray-400">({$i18n.t('one per line')})</span></span
									>
									{#if field.value === 'facts'}
										<textarea
											class="min-h-24 resize-y rounded-xl border border-gray-200 bg-transparent px-3 py-2 text-sm dark:border-gray-700"
											bind:value={factsText}
										></textarea>
									{:else if field.value === 'decisions'}
										<textarea
											class="min-h-24 resize-y rounded-xl border border-gray-200 bg-transparent px-3 py-2 text-sm dark:border-gray-700"
											bind:value={decisionsText}
										></textarea>
									{:else if field.value === 'constraints'}
										<textarea
											class="min-h-24 resize-y rounded-xl border border-gray-200 bg-transparent px-3 py-2 text-sm dark:border-gray-700"
											bind:value={constraintsText}
										></textarea>
									{:else}
										<textarea
											class="min-h-24 resize-y rounded-xl border border-gray-200 bg-transparent px-3 py-2 text-sm dark:border-gray-700"
											bind:value={openQuestionsText}
										></textarea>
									{/if}
								</label>
							{/each}
						</div>
					</details>
				</div>

				<div class="mt-2 truncate text-xs text-gray-400" title={preview.source_title}>
					{$i18n.t('Source')}: {preview.source_title}
				</div>

				<div class="mt-5 flex flex-wrap items-center justify-between gap-2">
					<div>
						{#if preview.existing_id}
							<button
								class="rounded-full px-3 py-2 text-xs text-red-600 transition hover:bg-red-50 dark:hover:bg-red-950/30"
								type="button"
								on:click={remove}
							>
								{$i18n.t('Delete saved reference')}
							</button>
						{/if}
					</div>
					<div class="flex items-center gap-2">
						<button
							data-testid="reference-capsule-regenerate"
							class="rounded-full bg-gray-100 px-3.5 py-2 text-sm text-gray-800 transition hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700"
							type="button"
							on:click={() => loadPreview(true)}
						>
							{$i18n.t('Regenerate')}
						</button>
						<button
							data-testid="reference-capsule-save"
							class="rounded-full bg-black px-4 py-2 text-sm text-white transition hover:bg-gray-900 disabled:opacity-50 dark:bg-white dark:text-black"
							type="button"
							disabled={saving}
							on:click={save}
						>
							{saving ? $i18n.t('Saving...') : $i18n.t('Save Reference')}
						</button>
					</div>
				</div>
			</div>
		{/if}
	</div>
</Modal>
