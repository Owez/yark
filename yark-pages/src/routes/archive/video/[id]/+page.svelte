<script lang="ts">
	import { getCurrentElement } from '$lib/element';
	import ArchiveCode from '../../../../components/video/ArchiveCode.svelte';
	import BackButton from '../../../../components/video/BackButton.svelte';
	import Description from '../../../../components/video/Description.svelte';
	import Graph from '../../../../components/video/Graph.svelte';
	import History from '../../../../components/video/History.svelte';
	import Player from '../../../../components/video/Player.svelte';
	import TopInfo from '../../../../components/video/TopInfo.svelte';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<!-- Core content -->
<BackButton />
<Player videoId={data.videoId} />
<h1 class="video">{getCurrentElement(data.video.title)}</h1>
<TopInfo videoId={data.videoId} video={data.video} />
<Description video={data.video} />
<!-- ~Below page fold -->
<History video={data.video} />
<Graph name="views" trackedElement={data.video.views} />
<Graph name="likes" trackedElement={data.video.likes} colour={1} />
<ArchiveCode videoRawArchive={data.videoRawArchive} />
<div class="spacer" />

<style lang="scss">
	.spacer {
		margin-bottom: 1rem;
	}
</style>
