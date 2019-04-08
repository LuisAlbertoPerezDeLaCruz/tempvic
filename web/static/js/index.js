$(document).ready(function() {

  $.fn.extend({
    slide: function () {
      var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';

      var $this = $(this), $active = $this.siblings('.active') || null, $container = $this.parent();

      var transOut = $this.index() > $active.index() ? 'slideOutLeft' : 'slideOutRight';

      var transIn = $this.index() > $active.index() ? 'slideInRight' : 'slideInLeft';


      if($active){
        $active.addClass('animated '+ transOut).one(animationEnd, function() {
          $active.removeClass('active animated '+ transOut);
        });
      }
      $this.removeClass('slideOutRight').removeClass('slideOutLeft').addClass('animated ' + transIn).one(animationEnd, function() {
          $this.removeClass('animated ' + transIn).addClass('active');
          $container.height($this.outerHeight());
      });
    }
  });

  $('.c8y-wizard-panel').eq(0).slide();

  $('.c8y-wizard-nav .back').click(function(e){
      e.preventDefault();
      var $target = $(this).closest('.c8y-wizard-panel').index() - 1;
      $('.c8y-wizard-panel').eq($target).slide();
  });

  $('[data-trigger="slide"]').click(function(e){
    e.preventDefault();
    $($(this).data('target')).slide();
  });
});