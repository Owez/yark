<script lang="ts">
	import { loadArchive } from '$lib/archive';
	import Dropzone from '../../../components/Dropzone.svelte';
	import LoadList from '../../../components/start/LoadList.svelte';
	import StartCard from '../../../components/start/StartCard.svelte';

	let path: string;
	$: loadArchive(path);
</script>

<div class="container">
	<StartCard
		title="Load Existing"
		description="Manage/view an existing archive that you've already created"
		ballKind={1}
		width={`${18 * 2 + 6 + 0.1}rem`}
	>
		<h2>Archive Folder</h2>
		<Dropzone bind:path />
		<h2>Recent</h2>
		<LoadList count={10} />
	</StartCard>
</div>

<style lang="scss">
	.container {
		display: flex;
		justify-content: center;
	}

	h2 {
		margin: 0;
		font-size: small;
		font-weight: 400;
	}
</style>
