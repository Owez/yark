<script lang="ts">
	import { StartCardState } from '$lib/components';

	export let margin = '0 0 0 0';
	export let startCard: StartCardState = StartCardState.None;
	export let mini = false;

	// Set the typical start card max margin automatically
	if (startCard == StartCardState.Max) {
		margin = '1.5rem 0 3rem 0';
	}
</script>

<div
	style:margin
	class="card card-border"
	class:start-card-normal={startCard == StartCardState.Enabled}
	class:start-card-max={startCard == StartCardState.Max}
	class:mini
>
	<slot />
</div>

<style lang="scss">
	$start-card-width: 18rem;
	$start-card-margin: 1.5rem;

	.card {
		border-radius: 7.5px;
		padding: $start-card-margin;
		padding-bottom: 0;
	}

	@mixin start-card {
		flex-shrink: 0;
		border-radius: 15px;
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

	.mini {
		$padding-v: 1rem;

		padding-top: $padding-v;
		padding-bottom: $padding-v;
		max-width: 30rem;
	}
</style>
