<script lang="ts">
	import { capitalizeFirstLetter, humanDate } from '$lib/utils';

	export let name: string;
	export let entry: [string, any];
	export let ind: number;
	export let lastEntry: number;

	let showing = false;

	$: nameCapitalized = capitalizeFirstLetter(name);
	$: isoString = entry[0];
	$: value = entry[1];
</script>

<li>
	{nameCapitalized}
	{#if ind == lastEntry}finally changed to{:else if ind == 0}was originally{:else}changed to{/if}
	<button class="bright" on:click={() => (showing = !showing)}>
		{#if showing}Hide{:else}Show{/if}
		{nameCapitalized}
	</button>
	on {humanDate(new Date(isoString))}
	{#if showing}
		<br />
		<div class="value">
			{#each value.split('\n') as line}
				{line}
			{/each}
		</div>
	{/if}
</li>

<style lang="scss">
	.value {
		color: #7f7f7f;
		margin-bottom: 0.35rem;
		margin-left: 0.5rem;
		font-size: smaller;
		line-height: 1.25rem;
		width: 30rem;
	}
</style>
