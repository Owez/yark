<script lang="ts">
	import { goto } from '$app/navigation';
	import { archiveVideoKindToString, getOpenedArchiveAlways } from '$lib/archive';
	import { capitalizeFirstLetter } from '$lib/utils';
	import Card from '../../../components/Card.svelte';
	import VideoBrief from '../../../components/VideoBrief.svelte';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<h1 class="title">
	{capitalizeFirstLetter(archiveVideoKindToString(data.kind))}
	<p>{getOpenedArchiveAlways().slug}</p>
</h1>
{#if data.videos.length > 1}
	<div class="videos">
		{#each data.videos as video}
			<VideoBrief {video} />
		{/each}
	</div>
{:else}
	<p>Sorry, there aren't any {archiveVideoKindToString(data.kind)} in this archive yet!</p>
	<button class="bright refresh" on:click={() => goto('/archive/dashboard')}
		>Go to dashboard?</button
	>
{/if}

<style lang="scss">
	h1 {
		display: flex;
		align-items: flex-end;

		p {
			font-size: x-small;
			font-weight: 500;
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

	button.refresh {
		margin-top: 0.65rem;
	}
</style>
