<script lang="ts">
	import { loadArchive } from '$lib/archive';
	import { StartCardState } from '$lib/components';
	import { yarkStore, type YarkStore } from '$lib/store';
	import Dropzone from '../../../../components/Dropzone.svelte';
	import LoadList from '../../../../components/start/LoadList.svelte';
	import StartCard from '../../../../components/start/StartCard.svelte';

	let path: string|undefined;
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
		description="Manage or view an archive that's already been made"
		ballKind={1}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">Import Folder</h2>
		<Dropzone bind:path />
		{#if anyRecents($yarkStore)}
			<h2 class="card-heading">Recent</h2>
			<LoadList count={10} />
		{/if}
	</StartCard>
</div>
