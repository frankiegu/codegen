<?php

class RESTPlugin extends Yaf_Plugin_Abstract {
    protected $allowMethods = array('get','post');
    protected $denyRedirectURL = '';
    protected $denyMsg = '';
    public function preDispatch(Yaf_Request_Abstract $request, Yaf_Response_Abstract $response) {
        $actionName = $request->getActionName();
        $curMethod = strtolower($request->getMethod());
        if (in_array($curMethod,$this->allowMethods))
        {
            $request->setActionName($actionName . ucfirst($curMethod));
        }else{
            if ($this->denyRedirectURL)
            {
                $response->setRedirect($this->denyRedirectURL);
            } else{
                die($this->denyMsg);
            }
        }
    }

    public function setAllowMethods($methods)
    {
        if (is_array($methods))
        {
            $methods = array_map('strtolower',$methods);
            $this->allowMethods = array_merge($methods);
        }else{
            $this->allowMethods[] = strtolower( $methods );
        }
    }

    public function setDenyRedirectURL($url)
    {
        $this->denyRedirectURL = $url;
    }

    public function setDenyMsg($msg)
    {
        $this->denyMsg = $msg;
    }
}
