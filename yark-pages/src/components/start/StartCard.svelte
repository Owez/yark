<script lang="ts">
	import Ball from '../Ball.svelte';

	export let ballKind: number;
	export let title: string = 'Start Card';
	export let description: string =
		'This is an example of a start card which is part of the Yark design';
</script>

<div class="card">
	<Ball kind={ballKind} />
	<h1>{title}</h1>
	<p class="description">{description}</p>
	<slot />
</div>

<style lang="scss">
	.card {
		height: 62.5vh; 
		width: 18rem;
		margin: 1.5rem;
		border: 1px solid rgba($color: #000000, $alpha: 0.12);
		border-radius: 15px;
		padding: 1.5rem;
	}

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
