<script lang="ts">
	import { loadArchive } from '$lib/archive';
	import { StartCardState } from '$lib/components';
	import { yarkStore, type YarkStore } from '$lib/store';
	import Dropzone from '../../../../components/Dropzone.svelte';
	import LoadList from '../../../../components/start/LoadList.svelte';
	import StartCard from '../../../../components/start/StartCard.svelte';

	let path: string;
	$: loadArchive(path);

	/**
	 * Checks if there are any recent archives
	 * @param store The Yark store to check
	 */
	function anyRecents(store: YarkStore): boolean {
		return store.recents.length != 0;
	}
</script>

<div class="centre-h">
	<StartCard
		title="Load Existing"
		description="Manage/view an existing archive that you've already created"
		ballKind={1}
		state={StartCardState.Max}
		margin="1.5rem 0 3rem 0"
	>
		<h2>Import Folder</h2>
		<Dropzone bind:path />
		{#if anyRecents($yarkStore)}
			<h2>Recent</h2>
			<LoadList count={10} />
		{/if}
	</StartCard>
</div>

<style lang="scss">
	h2 {
		margin: 0;
		font-size: small;
		font-weight: 400;
		color: rgb(99, 99, 99);
	}
</style>
