<script lang="ts">
	import { getVideoFileApiLink, videoWasUpdated } from '$lib/archive';
	import { getCurrentElement } from '$lib/element';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<p class="back-button">
	<a href="/archive/videos" class="invis">
		<img src="/img/btnback.svg" alt="Back" />
		<span class="text">Back</span>
	</a>
</p>
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
		<span>{data.video.uploaded}</span>
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

<style lang="scss">
	$medium: 765px;
	$large: 1300px;

	.back-button {
		$margin-v: 3rem;
		$padding-v: 1rem;

		margin: 0;
		margin-top: $margin-v - $padding-v;
		padding-bottom: $padding-v * 0.5;

		.text {
			font-size: smaller;
			margin-left: 0.3rem;
			font-weight: 500;
			color: #666766;
			padding-top: $padding-v;
			padding-right: 3rem;
		}
	}

	video {
		background-color: black;
		border-radius: 7.5px;
		aspect-ratio: 16/9;
	}

	h1 {
		font-size: x-large;
		font-weight: 450;
		margin-top: 0.5rem;
	}

	.info {
		color: #7f7f7f;
		display: flex;
		justify-content: space-between;
		font-size: 0.925rem;

		.spacer {
			margin-left: 0.35rem;
			margin-right: 0.35rem;
		}
	}

	@media (max-width: $medium) {
		video,
		.info {
			width: 25rem;
		}
	}

	@media (min-width: $medium) and (max-width: $large) {
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
