import React, { FC, useContext } from "react";
import Image from 'next/image'

const biosnicarLogo = () => {
  return (
    <>
      <Image src='/static/biosnicar-logo.png' alt=" " width="80" height="80" />
      &nbsp;&nbsp; <b>biosnicar</b>
    </>
  )
}

export { biosnicarLogo }