<script lang="ts">
	import type{  Archive } from '$lib/archive';
	import { readDir } from '@tauri-apps/api/fs';

	export let archive: Archive;

	/**
	 * Checks if the provided archive exists at it's current path
	 */
	async function checkArchiveExists(archive: Archive): Promise<boolean> {
		// Try to get directory and then check if the archive file is present
		try {
			// Try to get the directory
			const fileList = await readDir(archive.path);

			// Return true if the archive file is present
			for (let ind = 0; ind < fileList.length; ind++) {
				const file = fileList[ind];
				if (file.name == 'yark.json') {
					return true;
				}
			}

			// Nothing was found
			return false;
		} catch (error) {
			// Filesystem error of some kind
			return false;
		}
	}
</script>

<button on:click={() => archive.setAsCurrent()}>
	<p class="archive-name">{archive.slug}</p>
	{#await checkArchiveExists(archive) then exists}
		{#if !exists}
			<p title="This isn't a valid archive">❌</p>
		{/if}
	{/await}
</button>

<style lang="scss">
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
		display: flex;
		justify-content: space-between;
		cursor: pointer;
	}

	.archive-name {
		max-width: 15rem;
		overflow: hidden;
		white-space: nowrap;
		text-overflow: ellipsis;
	}
</style>
