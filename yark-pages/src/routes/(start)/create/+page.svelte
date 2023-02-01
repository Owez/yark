<script lang="ts">
	import { StartCardState } from '$lib/components';
	import StartCard from '../../../components/start/StartCard.svelte';

	let url: string;

	/**
	 * Checks if the input url is currently a channel
	 */
	function urlIsChannel(): boolean {
		return false; // TODO
	}

	/**
	 * Checks if the input url is currently a playlist
	 */
	function urlIsPlaylist(): boolean {
		return false; // TODO
	}
</script>

<div class="centre-h">
	<StartCard
		title="Create"
		description="Create an archive from scratch to save your channels + playlists"
		ballKind={0}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">YouTube URL</h2>
		<input
			type="text"
			name="create-url"
			class="max"
			placeholder="e.g. https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
			bind:value={url}
		/>
		<div class="url-types">
			<button class="url-type" class:active={urlIsChannel()}>Channel</button>
			<button class="url-type" class:active={urlIsPlaylist()}>Playlist</button>
		</div>
		<h2 class="card-heading">Save To</h2>
		<!-- TODO -->
	</StartCard>
</div>

<style lang="scss">
	$full-width: 30rem;

	.max {
		width: $full-width;
	}

	.url-types {
		display: flex;
	}

	.url-type {
		$spacing: 0.5rem;

		width: calc($full-width / 2 + 4.5px);
		height: 1.8rem;
		background-color: transparent;
		border: 1px solid rgba($color: #000000, $alpha: 0.12);
		border-radius: 5px;
		margin-right: $spacing;
	}
</style>
