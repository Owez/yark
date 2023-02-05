<script lang="ts">
	import { truncate } from '$lib/utils';
	import { open } from '@tauri-apps/api/dialog';

	export let path: string;
	export let pathCompletelyInvalid: boolean = false;

	/**
	 * Gets directory from tauri dialog and pipes into the path prop
	 */
	async function getDir() {
		// Get path from tauri
		const gotPath = await open({ directory: true });

		// They clicked out of the menu without giving a path
		if (gotPath == null) {
			pathCompletelyInvalid = path == undefined || path == '';
		}

		// Get first path if multiple are selected
		else if (Array.isArray(gotPath)) {
			pathCompletelyInvalid = false;
			path = gotPath[0];
		}

		// Get path if one is selected
		else {
			pathCompletelyInvalid = false;
			path = gotPath;
		}
	}
</script>

<button class="bright" on:click={async () => await getDir()} class:invalid={pathCompletelyInvalid}>
	{#if path == undefined}
		Select Folder..
	{:else}
		{truncate(path, 50)}
	{/if}
</button>
