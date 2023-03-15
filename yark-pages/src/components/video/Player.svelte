<script lang="ts">
	import { getVideoFileApiLink } from '$lib/archive';

	export let videoId: string;
</script>

<!-- NOTE: the ignore is a workaround for <https://github.com/sveltejs/svelte/issues/5967> -->
<!-- svelte-ignore a11y-media-has-caption -->
<video controls autoplay title="Video player">
	<source src={getVideoFileApiLink(videoId)} />
</video>

<style lang="scss">
	$large: 1300px;
	$grey: #7f7f7f;

	video {
		background-color: black;
		border-radius: 7.5px;
		aspect-ratio: 16/9;
	}

	@media (max-width: $large) {
		video {
			width: 40rem;
		}
	}

	@media (min-width: $large) {
		video {
			width: 55rem;
		}
	}
</style>
