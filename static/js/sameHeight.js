// JavaScript Document
(function(){
    var max = 0,
    dia = $('.dia');
    dia.each(function(v, i){
      height = $(i).height() + 30;
      height > max ? max = height : false
    });
	//console.log(max)
    dia.each(function(v, i){
      $(i).css('height', max + 30);
    })
  })();
  
  (function(){
    var max = 0,
    foto = $('.foto');
    foto.each(function(v, i){
      height = $(i).height() + 30;
      height > max ? max = height : false
    });
	//console.log(max)
    foto.each(function(v, i){
      $(i).css('height', max);
    })
  })();
  
  (function(){
    var max = 0,
    same = $('.same');
    same.each(function(v, i){
      height = $(i).height() + 30;
      height > max ? max = height : false
    });
	//console.log(max)
    same.each(function(v, i){
      $(i).css('height', max);
    })
  })();