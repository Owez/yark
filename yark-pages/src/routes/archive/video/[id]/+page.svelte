<script lang="ts">
	import { getVideoFileApiLink } from '$lib/archive';
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
<video width="320" height="240" controls>
	<source src={getVideoFileApiLink(data.id)} type="video/mp4"  />
</video>

<style lang="scss">
	.back-button {
		$margin-v: 3rem;
		$padding-v: 1rem;

		margin: 0;
		margin-top: $margin-v - $padding-v;

		.text {
			font-size: smaller;
			margin-left: 0.3rem;
			font-weight: 500;
			color: #666766;
			padding-top: $padding-v;
			padding-right: 3rem;
		}
	}
</style>
