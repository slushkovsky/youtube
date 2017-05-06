$(document).ready(function() {

	// menu collapse
	$('.page-header-collapse').click(function() {
		$('.page-header-nav').toggleClass('page-header-responsive');
		$('.btn-nav-collapse').toggleClass('btn-nav-collapse-opened');
	});

	// anchors' animation
	$('a').click(function(){
		$('html, body').animate({
			scrollTop: $( $(this).attr('href') ).offset().top
		}, 600);
		return false;
	});


	// opening pay window
	$('.select-tariff').click(function() {

		var tariffPlanType = $(this).data('tariffType');
		var tariffPrice = $(this).data('price');

		$('.pay-window').attr("aria-hidden", false);
		$('#tariff-plan-type').html(tariffPlanType);
		$('#final-price').html(tariffPrice + " руб.");

	});

	$('.close-pay-window').click(function() {
		$('.pay-window').attr("aria-hidden", true);
	});


	// Handling form submition
	$( "#pay-form" ).submit(function(event) {

	  event.preventDefault();

	  if ( $('#pay-name').val() && $('#pay-email').val() && $('#pay-email').is(':valid') && $('#checkbox').is(':checked')) {
	  	$('.pay-window').attr("aria-hidden", true);

	  	clearPayField();

	  	$('.pay-success').css({'display': 'block'})
	  	setTimeout(function() {
	  		$('.pay-success').css({'display': 'none'})
	  	}, 2500);

	  } else if ( ! ($('#checkbox').is(':checked'))) {
	  	$('.accept-offer').css({'display': 'block'})
	  	setTimeout(function() {
	  		$('.accept-offer').css({'display': 'none'})
	  	}, 1250);
	  	
	  } else {
	  	$('.wrong-data').css({'display': 'block'})
	  	setTimeout(function() {
	  		$('.wrong-data').css({'display': 'none'})
	  	}, 1250);
	  } 

	});

	function clearPayField() {
		$('#pay-name').val('');
		$('#pay-email').val('');
	}

	


});


