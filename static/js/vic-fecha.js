function vicFechaEstaSemana() {

	 var date = new  Date()
	 var p = new Date(date.setDate(date.getDate() - date.getDay()+1));
	 var u = new Date(date.setDate(date.getDate() - date.getDay()+6));
	 pfd = p.getDate() < 10 ? "0"+p.getDate():p.getDate();
	 pfm = p.getMonth() < 10 ? "0"+(p.getMonth()  + 1 ):(p.getMonth()  + 1 );
	 pfy = p.getFullYear();

	 sfd = u.getDate() < 10 ? "0"+u.getDate():u.getDate();
	 sfm = u.getMonth() < 10 ? "0"+(u.getMonth() + 1):(u.getMonth()  + 1 );
	 sfy = u.getFullYear();

	 $("#fechaInicio").val(pfd+"/"+pfm+"/"+pfy);
	 $("#fechaFinalizacion").val(sfd+"/"+sfm+"/"+sfy);
}

function vicFechaMes(){
	
	var date = new  Date()
	 var p = new Date(date.getFullYear(), date.getMonth(), 1);
	 var u = new Date(date.getFullYear(), date.getMonth()+1, 0);
	  
	 pfd = p.getDate() < 10 ? "0"+p.getDate():p.getDate();
	 pfm = p.getMonth() < 10 ? "0"+(p.getMonth()  + 1 ):(p.getMonth()  + 1 );
	 pfy = p.getFullYear();
	 
	 sfd = u.getDate() < 10 ? "0"+u.getDate():u.getDate();
	 sfm = u.getMonth() < 10 ? "0"+(u.getMonth() + 1):(u.getMonth()  + 1 );
	 sfy = u.getFullYear();
	 
	 $("#fechaInicio").val(pfd+"/"+pfm+"/"+pfy);
	 $("#fechaFinalizacion").val(sfd+"/"+sfm+"/"+sfy);
	
}

function vicFechaMesPasado(){
	
	var date = new  Date()
	 var p = new Date(date.getFullYear(), date.getMonth(), 1);
	 var u = new Date(date.getFullYear(), date.getMonth() , 0);
	  
	 pfd = p.getDate() < 10 ? "0"+p.getDate():p.getDate();
	 pfm = p.getMonth() < 10 ? "0"+(p.getMonth()):p.getMonth();
	 pfy = p.getFullYear();
	 
	 sfd = u.getDate() < 10 ? "0"+u.getDate():u.getDate();
	 sfm = u.getMonth() < 10 ? "0"+(u.getMonth() +1):(u.getMonth() +1);
	 sfy = u.getFullYear();
	 
	 $("#fechaInicio").val(pfd+"/"+pfm+"/"+pfy);
	 $("#fechaFinalizacion").val(sfd+"/"+sfm+"/"+sfy);
	
}

function vicFechaUlimosNoventa(){
	
	 
	var date = new  Date();
	date.setDate(date.getDate() - 90);
	
	 var p = date;
	 var u = new Date();
	  
	 pfd = p.getDate() < 10 ? "0"+ p.getDate() : p.getDate();
	 pfm = p.getMonth() < 10 ? "0"+(p.getMonth() + 1): (p.getMonth() + 1);
	 pfy = p.getFullYear();
	
	 sfd = u.getDate() < 10 ? "0"+u.getDate():u.getDate();
	 sfm = u.getMonth() < 10 ? "0"+(u.getMonth() + 1) :(u.getMonth() + 1);
	 sfy = u.getFullYear();
	 
	 
	 $("#fechaInicio").val(pfd+"/"+pfm+"/"+pfy);
	 $("#fechaFinalizacion").val(sfd+"/"+sfm+"/"+sfy);
	
}

function vicFechaUlimosNoventa(){
	
	 
	var date = new  Date();
	date.setDate(date.getDate() - 90);
	
	 var p = date;
	 var u = new Date();
	  
	 pfd = p.getDate() < 10 ? "0"+ p.getDate() : p.getDate();
	 pfm = p.getMonth() < 10 ? "0"+(p.getMonth() + 1): (p.getMonth() + 1);
	 pfy = p.getFullYear();
	
	 sfd = u.getDate() < 10 ? "0"+u.getDate():u.getDate();
	 sfm = u.getMonth() < 10 ? "0"+(u.getMonth() + 1) :(u.getMonth() + 1);
	 sfy = u.getFullYear();
	 
	 
	 $("#fechaInicio").val(pfd+"/"+pfm+"/"+pfy);
	 $("#fechaFinalizacion").val(sfd+"/"+sfm+"/"+sfy);

}


function vicFechaEsteAgno(){
	
	 
	 var date = new  Date();	
	 var p = new Date(date.getFullYear(), 0, 1);
	 var u = new Date(date.getFullYear(), 11, 31);

	 pfd = p.getDate() < 10 ? "0"+ p.getDate() : p.getDate();
	 pfm = p.getMonth() < 10 ? "0"+(p.getMonth() + 1): (p.getMonth() + 1);
	 pfy = p.getFullYear();
	
	 sfd = u.getDate() < 10 ? "0"+u.getDate():u.getDate();
	 sfm = u.getMonth() < 10 ? "0"+(u.getMonth() + 1) :(u.getMonth() + 1);
	 sfy = u.getFullYear();
	 
	 $("#fechaInicio").val(pfd+"/"+pfm+"/"+pfy);
	 $("#fechaFinalizacion").val(sfd+"/"+sfm+"/"+sfy);
	 
}


function vicFechaAgnoPasado(){
	
	 
	 var date = new  Date();	
	 var p = new Date(date.getFullYear()-1, 0, 1);
	 var u = new Date(date.getFullYear()-1, 11, 31);
	  
	 pfd = p.getDate() < 10 ? "0"+ p.getDate() : p.getDate();
	 pfm = p.getMonth() < 10 ? "0"+(p.getMonth() + 1): (p.getMonth() + 1);
	 pfy = p.getFullYear();
	
	 sfd = u.getDate() < 10 ? "0"+u.getDate():u.getDate();
	 sfm = u.getMonth() < 10 ? "0"+(u.getMonth() + 1) :(u.getMonth() + 1);
	 sfy = u.getFullYear();
	 
	 
	 $("#fechaInicio").val(pfd+"/"+pfm+"/"+pfy);
	 $("#fechaFinalizacion").val(sfd+"/"+sfm+"/"+sfy);
	 
}

function vicProximas(){
	$("#fechaInicio").val( $("#fechaInicialVigentes").val());
	$("#fechaFinalizacion").val($("#fechaFinalVigentes").val());
}

function vicProximasPlanificadas(){

	 var date = new  Date()
	 var p = new Date();
	 var u = new Date(date.setDate(date.getDate() + 15));

	 pfd = p.getDate() < 10 ? "0"+ p.getDate() : p.getDate();
	 pfm = p.getMonth() < 10 ? "0"+(p.getMonth() + 1): (p.getMonth() + 1);
	 pfy = p.getFullYear();

	 sfd = u.getDate() < 10 ? "0"+u.getDate():u.getDate();
	 sfm = u.getMonth() < 10 ? "0"+(u.getMonth() + 1) :(u.getMonth() + 1);
	 sfy = u.getFullYear();


	 $("#fechaInicio").val(pfd+"/"+pfm+"/"+pfy);
	 $("#fechaFinalizacion").val(sfd+"/"+sfm+"/"+sfy);

}

