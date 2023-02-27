<script lang="ts">
	import { capitalizeFirstLetter, humanDateFromIso } from '$lib/utils';

	export let name: string;
	export let entry: [string, string];
	export let ind: number;

	let showing = false;

	$: nameCapitalized = capitalizeFirstLetter(name);
	$: date = entry[0];
	$: value = entry[1];
</script>

<li>
	{nameCapitalized}
	{#if ind == 0}was originally{:else}changed to{/if}
	<button class="bright" on:click={() => (showing = !showing)}>
		{#if showing}Hide{:else}Show{/if}
		{nameCapitalized}
	</button>
	on {humanDateFromIso(date)}
	{#if showing}
		<br />
		<span class="value">
			{#each value.split('\n') as line}
				{line}
			{/each}
		</span>
	{/if}
</li>

<style lang="scss">
	.value {
		color: #7f7f7f;
		margin-top: 0.25rem;
		font-size: smaller;
		line-height: 1.25rem;
	}
</style>
