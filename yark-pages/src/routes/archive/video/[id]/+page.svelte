<script lang="ts">
	import { getVideoFileApiLink } from '$lib/archive';
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
<div class="info">
	<h1>{getCurrentElement(data.video.title)}</h1>
</div>

<style lang="scss">
	$medium: 765px;
	$large: 1300px;

	.back-button {
		$margin-v: 3rem;
		$padding-v: 1rem;

		margin: 0;
		margin-top: $margin-v - $padding-v;
		padding-bottom: $padding-v * 0.75;

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
		background-color: #666666;
		border-radius: 7.5px;
		aspect-ratio: 16/9;
		max-height: 70vh;
	}

	.info {
		h1 {
			font-size: x-large;
			font-weight: 450;
			margin-top:0.25rem;
		}
	}

	@media (max-width: $medium) {
		video {
			max-width: 25rem;
		}
	}

	@media (min-width: $medium) and (max-width: $large) {
		video {
			max-width: 40rem;
		}
	}

	@media (min-width: $large) {
		video {
			max-width: 60rem;
		}
	}
</style>
