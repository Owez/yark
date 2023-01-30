<script lang="ts">
	export let overflow: boolean = false;
	export let startCard: boolean = true;
	export let startCardHalf: boolean = true;
</script>

<div class="card" class:overflow class:start-card={startCard} class:start-card-half={startCardHalf}>
	<slot />
</div>

<style lang="scss">
	$start-card-height-full: 70vh;
	$margin: 1.5rem;

	.card {
		margin: $margin;
		border: 1px solid rgba($color: #000000, $alpha: 0.12);
		border-radius: 15px;
		padding: 1.5rem;
		padding-bottom: 0;
	}

	.overflow {
		overflow-y: auto;
	}

	.default {
		width: 10rem;
		height: 10rem;
	}

	.start-card {
		width: 18rem;
		height: $start-card-height-full;
	}

	.start-card-half {
		height: calc($start-card-height-full / 2 - $margin);
	}
</style>
