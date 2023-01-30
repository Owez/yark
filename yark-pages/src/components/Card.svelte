<script lang="ts">
	import { StartCardState } from '$lib/components';

	export let margin: string = '0 0 0 0';
	export let startCard: StartCardState = StartCardState.None;
</script>

<div
	style:margin
	class="card"
	class:start-card-full={startCard == StartCardState.Full}
	class:start-card-half={startCard == StartCardState.Half}
>
	<slot />
</div>

<style lang="scss">
	.card {
		border: 1px solid rgba($color: #000000, $alpha: 0.12);
		border-radius: 15px;
		padding: 1.5rem;
		padding-bottom: 0;
		box-shadow: rgba(100, 100, 111, 0.2) 0px 7px 29px 0px;
	}

	@mixin start-card {
		width: 18rem;
	}

	.start-card-full {
		@include start-card();
	}

	.start-card-half {
		@include start-card();
	}
</style>
