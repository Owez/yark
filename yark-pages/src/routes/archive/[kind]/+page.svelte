<script lang="ts">
	import { archiveVideoKindToString, getOpenedArchiveAlways } from '$lib/archive';
	import { capitalizeFirstLetter } from '$lib/utils';
	import Card from '../../../components/Card.svelte';
	import VideoBrief from '../../../components/VideoBrief.svelte';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="container">
	<div class="heading">
		<h1>
			{capitalizeFirstLetter(archiveVideoKindToString(data.kind))}
			<p>{getOpenedArchiveAlways().slug}</p>
		</h1>
	</div>
	{#if data.videos.length > 1}
		<div class="videos">
			{#each data.videos as video}
				<VideoBrief {video} />
			{/each}
		</div>
	{:else}
		<Card mini={true}>
			<p>Sorry, there aren't any {archiveVideoKindToString(data.kind)} in this archive yet!</p>
		</Card>
	{/if}
</div>

<style lang="scss">
	.container {
		$gap: 1rem;

		height: 100vh;
		overflow-y: auto;
		padding-left: $gap;
		padding-right: $gap;
	}

	h1 {
		font-size: 30px;
		font-weight: 500;
		margin-top: 3rem;
		margin-bottom: 1rem;
		display: flex;
		align-items: flex-end;

		p {
			font-size: x-small;
			font-weight: normal;
			color: gray;
			border: 0.5px solid gray;
			border-radius: 7.5px;
			padding: 3px;
			padding-left: 6px;
			padding-right: 6px;
			height: 0.9rem;
			margin-bottom: 0.5rem;
			margin-left: 0.6rem;
		}
	}

	.videos {
		display: flex;
		flex-wrap: wrap;
	}
</style>
