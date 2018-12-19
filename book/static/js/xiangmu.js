var app = angular.module('myApp',[]);
var csrftoken =$("meta[name=csrf-token]").attr("content");
$.ajaxSetup({
    headers: {"X-CSRFToken": csrftoken},
});
app.controller('myCtrl',function ($scope) {

    $scope.dengru01 = function(){
        $.post('/book/login/',{dyhm:$scope.usernameemail,dmm:$scope.dengrupassword},function (dengruxianshi) {
            if(dengruxianshi=="ok"){
                location.href='/book/index'
            }else {
                alert(dengruxianshi)
            }
        })
    };

    $scope.zhuce01 = function () {
        if($scope.username==undefined || $scope.Email==undefined || $scope.password==undefined || $scope.yianzhengma==undefined){
            alert("请输入正确的值！")
        }else {
            $.post('/book/zhuce01/',{yhm:$scope.username,yx:$scope.Email,mm:$scope.password,yzm:$scope.yianzhengma},function (zhucexianshi) {
                if(zhucexianshi=="ok"){
                    alert("注册成功请登录");
                    location.href="/book/login"
                }
            })
        }
    };

    $scope.mimachongzhi01 = function () {
        if($scope.Email==undefined || $scope.yianzhengma==undefined || $scope.password1==undefined || $scope.password2==undefined){
            alert("请输入正确的值！")
        }
        else {
            alert($scope.Email);
            $.post('/book/mimachongzhi01/',{zyhm:$scope.Email,zyx:$scope.yianzhengma,zxmm1:$scope.password1,zxmm2:$scope.password2},function (chongzhixianshi) {
                alert(chongzhixianshi)
            })
        }
    };

    $scope.dianjiyzm = function () {
        $.post("/book/dianjiyianzhengma/",{yx:$scope.Email},function (czyzm1) {
            alert(czyzm1)
        })
    }
});