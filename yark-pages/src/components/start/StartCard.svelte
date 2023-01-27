<script lang="ts">
	import Ball from '../Ball.svelte';
	import Card from '../Card.svelte';

	export let title: string = 'Start Card';
	export let description: string =
		'This is an example of a start card which is part of the Yark design';
	export let ballKind: number;
	export let width: string = '18rem';
	export let height: string = '62.5vh';
</script>

<Card {width} {height}>
	<Ball kind={ballKind} />
	<h1>{title}</h1>
	<p class="description">{description}</p>
	<slot />
</Card>

<style lang="scss">
	h1 {
		$margin-v: 0.75rem;

		font-size: 18pt;
		font-weight: 500;
		margin-top: $margin-v;
		margin-bottom: $margin-v;
	}

	.description {
		font-size: 12pt;
	}
</style>
