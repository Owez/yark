<script lang="ts">
	import { open } from '@tauri-apps/api/dialog';

	export let path: string;

	/**
	 * Gets file from tauri dialog and pipes into the path prop
	 */
	async function getFile() {
		const gotPath = await open();
		if (gotPath == null) {
			return;
		} else if (Array.isArray(gotPath)) {
			path = gotPath[0];
		} else {
			path = gotPath;
		}
	}
</script>

<button on:click={async () => await getFile()}>Drop/Browse</button>

<style lang="scss">
	button {
		width: 15rem;
		height: 4rem;
		border: 1.75px dashed #c2c2c2;
		border-radius: 7.5px;
		color: #8f8f8f;
		font-size: smaller;
		font-weight: 300;
		background-color: transparent;
		margin-top: 0.35rem;
		margin-bottom: 1rem;
	}
</style>
