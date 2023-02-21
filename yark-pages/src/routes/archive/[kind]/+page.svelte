<script lang="ts">
	import { archiveVideoKindToString } from '$lib/archive';
	import { yarkStore } from '$lib/store';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="container">
	<h1>{$yarkStore.openedArchive?.slug}'s {archiveVideoKindToString(data.kind)}</h1>
	{data.videos}
</div>

<style lang="scss">
	.container {
		$margin-h: 1rem;

		// No margin left because the sidebar has that
		margin-right: $margin-h;
	}
	h1 {
		margin-top: 10vh;
		font-size: 2.25rem;
		text-align: center;
	}
</style>
