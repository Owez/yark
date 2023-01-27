<script lang="ts">
	import { yarkStore } from '$lib/store';
	import { loadArchive, type Archive } from '$lib/yark';

	export let count: number = 4;

	/**
	 * Gets most recent archives up to the count
	 */
	function getArchives(recents: Archive[]): Archive[] {
		return recents.slice().reverse().slice(0, count);
	}

	/**
	 * Gets archive path from the provided filepath and then loads
	 * @param event Button event with `data-path` attached to target
	 */
	function listLoadArchive(event: any) {
		const filepath = event.target.getAttribute('data-path');
		loadArchive(filepath);
	}
</script>

<div class="list">
	{#each getArchives($yarkStore.recents) as archive}
		<button on:click={listLoadArchive} data-path={archive.path}>{archive.path}</button>
	{/each}
</div>

<style lang="scss">
	.list {
		margin-bottom: 1.25rem;
		display: flex;
		flex-direction: column;
	}

	button {
		$margin-v: 0.35rem;
		$padding-h: 0.75rem;

		background: rgb(255, 255, 255);
		background: linear-gradient(142deg, rgb(247, 247, 247) 0%, rgba(244, 244, 244, 1) 100%);
		height: 2rem;
		display: flex;
		align-items: center;
		margin-top: $margin-v;
		margin-bottom: $margin-v;
		padding-left: $padding-h;
		padding-right: $padding-h;
		border-radius: 7.5px;
		border: 0;
		background-color: transparent;
	}
</style>
