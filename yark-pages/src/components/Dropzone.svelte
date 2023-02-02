<script lang="ts">
	import { loadArchive } from '$lib/archive';
	import { open } from '@tauri-apps/api/dialog';
	import { listen } from '@tauri-apps/api/event';

	export let path: string | undefined;

	/**
	 * Gets directory from tauri dialog and pipes into the path prop
	 */
	async function getDir() {
		const gotPath = await open({ directory: true });
		if (gotPath == null) {
			return;
		} else if (Array.isArray(gotPath)) {
			path = gotPath[0];
		} else {
			path = gotPath;
		}
	}

	// Listen for drops anywhere onto the screen
	// NOTE: this is what you need to do because of a bad tauri implementation
	// 		 see #2768 <https://github.com/tauri-apps/tauri/issues/2768>
	//       see #4736 <https://github.com/tauri-apps/tauri/discussions/4736>
	// TODO: fix error where it loads like 5 times
	listen('tauri://file-drop', (event) => {
		const payload = event.payload as string[];
		const path = payload[0];
		loadArchive(path);
	});
</script>

<button on:click={getDir}>Drop/Browse</button>

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
