<script lang="ts">
	import { StartCardState } from '$lib/components';
	import StartCard from '../../../components/start/StartCard.svelte';

	let url: string | undefined;
	let name: string | undefined;

	let urlCompletelyInvalid: boolean = false;
	let nameCompletelyInvalid: boolean = false;
	let urlExpand: boolean = false;
	let saveDirectory: string | null = null;

	/**
	 * Checks if the input url is currently a channel
	 */
	function urlIsChannel(url?: string): boolean {
		// Make sure it isn't undefined
		if (url == undefined) {
			return false;
		}

		// Get patterns to check for
		const isAtPattern = /\..+\/@.+/.exec(url) != null;
		const isChannelPattern = /.+\/channel\/.+/.exec(url) != null;
		const isUserPattern = /.+\/user\/.+/.exec(url) != null;
		const isCPattern = /.+\/c\/.+/.exec(url) != null;

		// See if it matches one pattern
		const atLeastOne = isAtPattern || isChannelPattern || isUserPattern || isCPattern;

		// Return
		return atLeastOne;
	}

	/**
	 * Checks if the input url is currently a playlist
	 */
	function urlIsPlaylist(url?: string): boolean {
		// Make sure it isn't undefined
		if (url == undefined) {
			return false;
		}

		// Check
		return url.includes('?list=');
	}

	/**
	 * Fixes up the url so its a valid one to pull from
	 * @param url URL to fix up
	 */
	function fixUrl(url?: string): string | undefined {
		// Make sure it isn't undefined
		if (url == undefined) {
			return undefined;
		}

		// Make a new url store to save changes
		let newUrl = url;

		// Remove common mistakes from the url
		const hitList = [
			'/featured',
			'/videos',
			'/shorts',
			'/playlists',
			'/community',
			'/channels',
			'/about'
		];
		hitList.forEach((hit) => {
			newUrl = newUrl.replace(hit, '');
		});

		// Return
		return newUrl;
	}

	function checkUrlValidity(url: string | undefined): [string | undefined, boolean] {
		// Contract the url checks and return if its undefined
		if (url == undefined || url == '') {
			urlExpand = false;
			return [undefined, true];
		}

		// Fix the url up before we check
		const fixedUrl = fixUrl(url);

		// Check if it's incorrect
		let isIncorrect = !(urlIsChannel(fixedUrl) || urlIsPlaylist(fixedUrl));

		// Return
		return [fixedUrl, isIncorrect];
	}
</script>

<div class="centre-h">
	<StartCard
		title="Create Local"
		description="Create an archive from scratch to save channels/playlists"
		ballKind={0}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">Destination</h2>
		<button class="bright">
			{#if saveDirectory == null}
				Choose Folder
			{:else}
				{saveDirectory}
			{/if}
		</button>
		<span class="slash-indicator">/</span>
		<input
			type="text"
			name="create-name"
			placeholder="e.g. foobar"
			class="mini"
			bind:value={name}
			on:focusout={() => (nameCompletelyInvalid = name == undefined || name == '')}
			class:invalid={nameCompletelyInvalid}
		/>
		<h2 class="card-heading">YouTube URL</h2>
		<input
			type="text"
			name="create-url"
			class="max"
			placeholder="e.g. https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
			bind:value={url}
			on:keydown={() => (urlCompletelyInvalid = false)}
			on:focusout={() => ([url, urlCompletelyInvalid] = checkUrlValidity(url))}
			on:focusin={() => (urlExpand = true)}
			class:invalid={urlCompletelyInvalid}
		/>
		{#if urlExpand}
			<div class="url-types">
				<div class="url-type" class:active={urlIsChannel(url)}>Channel</div>
				<div class="url-type" class:active={urlIsPlaylist(url)}>Playlist</div>
			</div>
		{/if}
		<h2 class="card-heading">Continue</h2>
		<button class="bright bottom-element">Start Download</button>
	</StartCard>
</div>

<style lang="scss">
	$full-width: 30rem;

	.max {
		width: $full-width;
	}

	.url-types {
		display: flex;
		margin-bottom: 1rem;
	}

	.url-type {
		$spacing: 0.5rem;

		width: calc($full-width / 2 + 4.5px);
		height: 1.8rem;
		border: 1px solid rgba($color: #000000, $alpha: 0.12);
		border-radius: 5px;
		margin-right: $spacing;
		color: gray;
		display: flex;
		justify-content: center;
		align-items: center;
		font-size: 0.7rem;
	}

	.active {
		background: rgb(126, 155, 222);
		border: 1px solid white;
		color: white;
		font-weight: 500;
	}

	.invalid {
		border: 1px solid rgb(217, 89, 89);
	}

	.bottom-element {
		margin-bottom: 1.5rem;
	}
</style>
