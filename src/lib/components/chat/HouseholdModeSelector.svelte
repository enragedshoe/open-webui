<script lang="ts">
	export let webSearchEnabled = false;
	export let onWebSearchToggle: (enabled: boolean) => void = () => {};
</script>

<div
	id="household-web-search-control"
	class="px-2 pt-2 flex items-center justify-start text-[12px] leading-4 text-gray-600 dark:text-gray-300"
>
	<label class="flex cursor-pointer items-center gap-1.5 whitespace-nowrap">
		<input
			id="household-web-search"
			type="checkbox"
			class="size-3.5 cursor-pointer accent-sky-600"
			bind:checked={webSearchEnabled}
			on:change={() => onWebSearchToggle(webSearchEnabled)}
		/>
		<span>Search the web</span>
	</label>
</div>
