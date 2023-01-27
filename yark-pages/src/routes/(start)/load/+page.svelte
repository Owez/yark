<script lang="ts">
	import { loadArchive } from '$lib/yark';
	import LoadList from '../../../components/start/LoadList.svelte';
	import StartCard from '../../../components/start/StartCard.svelte';

	let filepath: string;
	$: loadArchive(filepath);
</script>

<div class="container">
	<StartCard
		title="Load Existing"
		description="Manage/view an existing archive that you've already created"
		ballKind={1}
		width={`${18 * 2 + 6 + 0.1}rem`}
	>
		<h2>Archive Folder</h2>
		<label for="archive-selector"><span>Drop/Browse</span></label>
		<input type="file" id="archive-selector" bind:value={filepath} />
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

	input[type='file'] {
		display: none;
	}

	label {
		width: 15rem;
		height: 4rem;
		border: 1.75px dashed #c2c2c2;
		border-radius: 7.5px;
		margin-top: 0.35rem;
		margin-bottom: 1rem;
		color: #8f8f8f;
		font-size: smaller;
		font-weight: 300;
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>
