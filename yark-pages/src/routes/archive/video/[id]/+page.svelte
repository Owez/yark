<script lang="ts">
	import { getVideoFileApiLink, videoWasUpdated } from '$lib/archive';
	import { getCurrentElement } from '$lib/element';
	import { humanDateFromIso } from '$lib/utils';
	import BackButton from '../../../../components/video/BackButton.svelte';
	import Description from '../../../../components/video/Description.svelte';
	import History from '../../../../components/video/History.svelte';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<BackButton />
<!-- NOTE: workaround for <https://github.com/sveltejs/svelte/issues/5967> -->
<!-- svelte-ignore a11y-media-has-caption -->
<video controls autoplay>
	<source src={getVideoFileApiLink(data.id)} type="video/mp4" />
</video>
<h1>{getCurrentElement(data.video.title)}</h1>
<div class="info">
	<p>
		<span>{getCurrentElement(data.video.views)} views</span>
		<span class="spacer">•</span>
		<span>{humanDateFromIso(data.video.uploaded)}</span>
		{#if videoWasUpdated(data.video)}
			<span class="spacer">•</span>
			<span>🌀</span>
		{/if}
	</p>
	<p>
		<a
			href={`https://www.youtube.com/watch?v=${data.id}`}
			target="_blank"
			rel="noopener noreferrer"
			class="invis">🔗</a
		>
		<span class="spacer">•</span>
		<a href={getVideoFileApiLink(data.id)} target="_blank" rel="noopener noreferrer" download>💾</a>
	</p>
</div>
<Description video={data.video} />
<h2>History</h2>
<History video={data.video} />

<style lang="scss">
	$large: 1300px;
	$grey: #7f7f7f;

	video {
		background-color: black;
		border-radius: 7.5px;
		aspect-ratio: 16/9;
	}

	h1,
	h2 {
		font-weight: 450;
	}

	h1 {
		font-size: x-large;
		margin-top: 0.75rem;
	}

	h2 {
		font-size: large;
		margin-top: 1rem;
		margin-bottom: 0.25rem;
	}

	.info {
		color: $grey;
		display: flex;
		justify-content: space-between;
		font-size: 0.925rem;
		line-height: 1.25rem;

		.spacer {
			margin-left: 0.35rem;
			margin-right: 0.35rem;
		}
	}

	@media (max-width: $large) {
		video,
		.info {
			width: 40rem;
		}
	}

	@media (min-width: $large) {
		video,
		.info {
			width: 55rem;
		}
	}
</style>
