<script lang="ts">
	import { StartCardState } from '$lib/components';

	export let margin: string = '0 0 0 0';
	export let startCard: StartCardState = StartCardState.None;
</script>

<div
	style:margin
	class="card"
	class:start-card={startCard == StartCardState.Enabled}
	class:start-card-max={startCard == StartCardState.Max}
>
	<slot />
</div>

<style lang="scss">
	$start-card-width: 18rem;
	$start-card-margin: 1.5rem;

	.card {
		border: 1px solid rgba($color: #000000, $alpha: 0.12);
		border-radius: 15px;
		padding: $start-card-margin;
		padding-bottom: 0;
		box-shadow: rgba(100, 100, 111, 0.2) 0px 7px 29px 0px;
	}

	.start-card {
		width: $start-card-width;
	}

	.start-card-max {
		$bodge: 2px;
		$padding: $start-card-margin * 2;
		width: calc($start-card-width * 2 + $start-card-margin + $padding + $bodge);
	}
</style>
