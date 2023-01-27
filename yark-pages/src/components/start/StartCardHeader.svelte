<script lang="ts">
	import Ball from '../Ball.svelte';

	export let title: string;
	export let description: string;
	export let ballKind: number;
</script>

<Ball kind={ballKind} />
<h1>{title}</h1>
<p class="description">{description}</p>

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
		margin-bottom: 1.5rem;
	}
</style>
