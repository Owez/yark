<script lang="ts">
	import { StartCardState } from '$lib/components';

	export let margin: string = '0 0 0 0';
	export let startCard: StartCardState = StartCardState.None;

	// Set the typical start card max margin automatically
	if (startCard == StartCardState.Max) {
		margin = '1.5rem 0 3rem 0';
	}
</script>

<div
	style:margin
	class="card"
	class:start-card-normal={startCard == StartCardState.Enabled}
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

	@mixin start-card {
		flex-shrink: 0;
	}

	.start-card-normal {
		@include start-card();

		width: $start-card-width;
	}

	.start-card-max {
		@include start-card();

		$bodge: 2px;
		$padding: $start-card-margin * 2;
		width: calc($start-card-width * 2 + $start-card-margin + $padding + $bodge);
	}
</style>
