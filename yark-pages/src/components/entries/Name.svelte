<script lang="ts">
	export let name: string;
	export let nameCompletelyInvalid: boolean = false;
	export let placeholder: string = 'Name';
</script>

<input
	type="text"
	{placeholder}
	class="mini"
	bind:value={name}
	on:focusout={() => (nameCompletelyInvalid = name == undefined || name == '')}
	class:invalid={nameCompletelyInvalid}
/>
